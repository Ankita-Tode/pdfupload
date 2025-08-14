import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import DocumentUploadForm
from .models import Document, ChatSession, ChatMessage
from .utils.rag import build_index, load_store, retrieve, assemble_prompt
from .utils.llm import chat as llm_chat

def home(request):
    return redirect("upload")

def upload(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc: Document = form.save(commit=False)
            doc.save()

            # Build FAISS index
            faiss_dir = os.path.join(settings.MEDIA_ROOT, f"indexes/doc_{doc.id}")
            os.makedirs(faiss_dir, exist_ok=True)

            index_path, meta_path, num_pages, num_chunks = build_index(
                pdf_path=doc.file.path,
                faiss_dir=faiss_dir,
                embed_model=settings.OPENAI_EMBED_MODEL,
                chunk_size=settings.CHUNK_SIZE,
                overlap=settings.CHUNK_OVERLAP,
            )

            doc.num_pages = num_pages
            doc.faiss_index_path = index_path
            doc.chunks_jsonl_path = meta_path
            doc.save()

            # New chat session per doc
            session = ChatSession.objects.create(document=doc)
            return redirect("chat", session_id=session.id)
    else:
        form = DocumentUploadForm()
    return render(request, "upload.html", {"form": form})

def chat_view(request, session_id: int):
    session = get_object_or_404(ChatSession, pk=session_id)
    doc = session.document
    messages = session.messages.order_by("created_at")
    return render(request, "chat.html", {"session": session, "doc": doc, "messages": messages})

@require_POST
def ask(request, session_id: int):
    session = get_object_or_404(ChatSession, pk=session_id)
    question = request.POST.get("question", "").strip()
    if not question:
        return HttpResponseBadRequest("Empty question.")

    doc = session.document
    faiss_dir = os.path.dirname(doc.faiss_index_path)

    vs = load_store(faiss_dir, settings.OPENAI_EMBED_MODEL)
    top_chunks = retrieve(vs, question, settings.OPENAI_EMBED_MODEL, top_k=settings.TOP_K)
    messages, context_block = assemble_prompt(
        settings.SYSTEM_PROMPT, question, top_chunks, max_tokens=settings.MAX_CONTEXT_TOKENS
    )
    answer = llm_chat(messages, model=settings.OPENAI_CHAT_MODEL)

    # Persist chat
    ChatMessage.objects.create(session=session, role="user", content=question)
    ChatMessage.objects.create(session=session, role="assistant", content=answer)

    return JsonResponse({
        "answer": answer,
        "sources": [{"pages": [c["page_start"]+1, c["page_end"]+1], "score": c["score"]} for c in top_chunks],
    })

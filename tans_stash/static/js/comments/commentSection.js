
const root = document.getElementById("comments-section");

const contentType = root?.dataset.contentType || null;
const contentId = root?.dataset.contentId
  ? Number(root.dataset.contentId)
  : null;

// Example check
if (!contentType || !contentId) {
  console.warn("Comments disabled: missing content data");
}

let currentPage = 1;
const perPage = 2;

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}

function formatDate(isoString) {
  const date = new Date(isoString);

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}


function renderComments(comments) {
    const container = document.getElementById("comments-container");
    container.innerHTML = "";
    if (comments.length === 0){
        container.innerHTML = '<i>"No comments yet. Be the first to comment."</i>'
    }
    comments.forEach(comment => {
        container.appendChild(createCommentElement(comment));
    });
}

function createCommentElement(comment) {
    const div = document.createElement("div");
    div.className = "comment";

    div.innerHTML = `
            <p><strong>${escapeHtml(comment.author_name)}</strong></p>
            <p>${escapeHtml(comment.comment)}</p>
            <small>${formatDate(comment.created_at)}</small>
            <!--<button onclick="showReplyForm(${comment.id})">Reply</button>
            <div class="replies"></div>-->
        `;

    // THIS IS THE RENDER REPLIES
    /* const repliesContainer = div.querySelector(".replies");

    if (comment.replies && comment.replies.length > 0) {
        comment.replies.forEach(reply => {
            repliesContainer.appendChild(createCommentElement(reply));
        });
    }*/

    return div;
}

function loadComments(page = 1) {
    fetch("/api/comments/get", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            content_type: contentType,
            content_id: contentId,
            page: page,
            per_page: perPage
        })
    })
        .then(res => res.json())
        .then(data => {
            console.log(data.message || "Everything Good!");
            renderComments(data.comments);
            updatePagination(data.pagination);
            currentPage = page;
        })
        .catch(err => {
            console.error("Error loading comments:", err);
        });

}

function submitComment(e) {
    e.preventDefault();

    fetch("/api/comment/put", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            content_type: contentType,
            content_id: contentId,
            author_name: document.getElementById("author_name").value,
            author_email: document.getElementById("author_email").value,
            comment: document.getElementById("comment_text").value
        })
    })
        .then(res => res.json())
        .then(() => {
            document.getElementById("comment-form").reset();
            loadComments();
        });
}

function updatePagination(pagination) {
    document.getElementById("pageInfo").innerText =
        `Page ${pagination.page} of ${pagination.pages}`;

    document.getElementById("prevBtn").disabled = !pagination.has_prev;
    document.getElementById("nextBtn").disabled = !pagination.has_next;

    document.getElementById("prevBtn").onclick = () =>
        loadComments(currentPage - 1);

    document.getElementById("nextBtn").onclick = () =>
        loadComments(currentPage + 1);
}

document.addEventListener("DOMContentLoaded", () => {
    loadComments();

    document.getElementById("comment-form").addEventListener("submit", submitComment);
});

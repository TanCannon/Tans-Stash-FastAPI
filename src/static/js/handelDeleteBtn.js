const deleteForm = document.getElementById("deletePostForm");

deleteForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const confirmed = confirm("Are you sure you want to delete this blog?");
    if (!confirmed) return;

    const postId = this.dataset.postId;

    try {
        const response = await fetch(`/api/delete-blog/${postId}`, {
            method: "DELETE",
            credentials: "include"
        });

        if (response.ok) {
            alert("Blog deleted successfully!");
            // window.location.href = "/admin"; // or reload
            window.location.reload();
        } else {
            alert("Failed to delete blog.");
        }

    } catch (err) {
        console.error(err);
        alert("Something went wrong.");
    }
});

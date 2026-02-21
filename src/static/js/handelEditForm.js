document.getElementById("editPostForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    // If using CKEditor 4
    if (typeof CKEDITOR !== "undefined") {
        CKEDITOR.instances.content.updateElement();
    }

    const formData = new FormData(this);

    const postId = formData.get("post_sno");

    const payload = {
        title: formData.get("title"),
        tag_line: formData.get("tline"),
        description: formData.get("description"),
        slug: formData.get("slug"),
        content: formData.get("content"),
        img_file: formData.get("img_file")
    };

    try {
        const response = await fetch(`/api/update-blog/${postId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Post edited successfully!");
            // window.location.href = "/admin"; // redirect if you want
        } else {
            // Handle error
            const errorData = await response.json();
            alert(`Error: ${errorData.detail}`);
        }
    } catch (err) {
        console.error(err);
        alert("Something went wrong");
    }
});

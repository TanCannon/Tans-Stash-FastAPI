document.getElementById("addPostForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    // If using CKEditor 4
    if (typeof CKEDITOR !== "undefined") {
        CKEDITOR.instances.content.updateElement();
    }

    const formData = new FormData(this);

    const payload = {
        title: formData.get("title"),
        tag_line: formData.get("tline"),
        description: formData.get("description"),
        slug: formData.get("slug"),
        content: formData.get("content"),
        img_file: formData.get("img_file")
    };

    try {
        const response = await fetch("/api/create-blog", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const data = await response.json();
            alert("Post created successfully!");
            // window.location.href = "/admin"; // redirect if you want
        } else {
            const error = await response.json();
            alert(error.detail || "Error occurred");
        }
    } catch (err) {
        console.error(err);
        alert("Something went wrong");
    }
});

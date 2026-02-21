const bannerForm = document.getElementById("postBannerUploadForm");

if (bannerForm) {
    bannerForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(this);

        try {
            const response = await fetch("/api/upload-blog-banner", {
                method: "POST",
                body: formData,
                credentials: "include" // VERY important for session auth
            });

            if (response.ok) {
                alert("Banner uploaded successfully!");
                bannerForm.reset();
            } else {
                const errorText = await response.text();
                alert(errorText || "Upload failed.");
            }

        } catch (err) {
            console.error(err);
            alert("Something went wrong.");
        }
    });
}

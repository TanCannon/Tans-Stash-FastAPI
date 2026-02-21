const logoutBtn = document.getElementById("dashboardLogoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/api/admin/logout", {
                method: "POST",
                credentials: "include"
            });

            if (response.ok) {
                // alert("Logged out successfully."); not good UX
                window.location.href = "/admin/login";
            } else {
                alert("Logout failed.");
            }

        } catch (error) {
            console.error("Error:", error);
            alert("Something went wrong.");
        }
    });
}

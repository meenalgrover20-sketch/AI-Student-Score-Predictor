// ===============================
// SEARCH HISTORY
// ===============================

const searchInput = document.getElementById("searchHistory");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        const rows = document.querySelectorAll("#historyBody tr");

        rows.forEach(row => {

            const text = row.innerText.toLowerCase();

            if (text.includes(value)) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    });

}

// ===============================
// CLEAR HISTORY
// ===============================

async function clearHistory() {

    const confirmDelete = confirm(
        "Are you sure you want to delete all prediction history?"
    );

    if (!confirmDelete) return;

    try {

        const response = await fetch("/clear_history", {

            method: "POST"

        });

        const data = await response.json();

        if (data.status === "success") {

            alert("History Cleared Successfully ✅");

            location.reload();

        } else {

            alert("Failed to clear history.");

        }

    }

    catch (error) {

        console.error(error);

        alert("Something went wrong.");

    }


}

function showAlert(icon, title, message){

    document.getElementById("alertIcon").innerHTML = icon;

    document.getElementById("alertTitle").innerHTML = title;

    document.getElementById("alertMessage").innerHTML = message;

    document.getElementById("customAlert").style.display = "flex";

}

function closeAlert(){

    document.getElementById("customAlert").style.display = "none";

}
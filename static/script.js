async function predictScore() {

    const hours = document.getElementById("hours").value;
    const attendance = document.getElementById("attendance").value;
    const previous = document.getElementById("previous").value;

    if (!hours || !attendance || !previous) {
        showAlert(
    "⚠️",
    "Missing Information",
    "Please fill all fields."
);

   return;
    }

    // ================= VALIDATION =================

if (hours < 0 || hours > 24) {

    showAlert(
        "⚠️",
        "Invalid Study Hours",
        "Study hours must be between 0 and 24."
    );

    return;

}

if (attendance < 0 || attendance > 100) {

    showAlert(
        "⚠️",
        "Invalid Attendance",
        "Attendance must be between 0 and 100%."
    );

    return;

}

if (previous < 0 || previous > 100) {

    showAlert(
        "⚠️",
        "Invalid Previous Score",
        "Previous score must be between 0 and 100."
    );

    return;

}

    const btn = document.querySelector(".predict-btn");

    btn.innerHTML = `
         <div class="btn-loader"></div>
        <span>Predicting...</span>
`;
    btn.disabled = true;

    try {

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                hours,
                attendance,
                previous
            })
        });

        if (!response.ok) {
            throw new Error("Prediction Failed");
        }

        await response.json();

        window.location.href = "/report";

    } catch (error) {

        console.error(error);
        alert("Prediction Failed");

    } finally {

        btn.innerHTML = "🚀 Predict My Score";
        btn.disabled = false;

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
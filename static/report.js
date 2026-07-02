console.log("Report JS Loaded");

window.addEventListener("load", () => {

    const canvas = document.getElementById("reportChart");

    if (!canvas) {
        console.log("Canvas not found");
        return;
    }

    const score = Number(canvas.dataset.score);

    console.log("Score =", score);

    new Chart(canvas, {
        type: "doughnut",

        data: {
            labels: ["Score", "Remaining"],

            datasets: [{
                data: [score, 100 - score],

                backgroundColor: [
                    "#7c3aed",
                    "#1e293b"
                ],

                borderWidth: 0
            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: "75%",

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {
                    enabled: false
                }

            },

            animation: {

                animateRotate: true,

                duration: 1800

            }

        }

    });

});

// ==========================
// DOWNLOAD PROFESSIONAL PDF
// ==========================

function downloadPDF() {

    const element = document.getElementById("pdfContent");

    // PDF banate waqt hidden template ko temporarily show karo
    element.style.display = "block";

    const options = {

        margin: 10,

        filename: "AI_Student_Performance_Report.pdf",

        image: {
            type: "jpeg",
            quality: 1
        },

        html2canvas: {
            scale: 2,
            useCORS: true
        },

        jsPDF: {
            unit: "mm",
            format: "a4",
            orientation: "portrait"
        }

    };

    html2pdf()
        .set(options)
        .from(element)
        .save()
        .then(() => {

            // PDF banne ke baad fir se hide kar do
            element.style.display = "none";

        })
        .catch((err) => {

            console.error(err);

            element.style.display = "none";

        });

}
const now = new Date();

document.getElementById("reportDate").innerHTML =
now.toLocaleDateString();

document.getElementById("reportTime").innerHTML =
now.toLocaleTimeString([],{
    hour:"2-digit",
    minute:"2-digit"
});

function showAlert(icon, title, message){

    document.getElementById("alertIcon").innerHTML = icon;

    document.getElementById("alertTitle").innerHTML = title;

    document.getElementById("alertMessage").innerHTML = message;

    document.getElementById("customAlert").style.display = "flex";

}

function closeAlert(){

    document.getElementById("customAlert").style.display = "none";

}
function showAlert(icon, title, message){

    document.getElementById("alertIcon").innerHTML = icon;

    document.getElementById("alertTitle").innerHTML = title;

    document.getElementById("alertMessage").innerHTML = message;

    document.getElementById("customAlert").style.display = "flex";

}

function closeAlert(){

    document.getElementById("customAlert").style.display = "none";

}
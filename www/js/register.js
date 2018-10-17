function submitNickname(){
    var approvemsg = "You are logged in.";
    var emptynickmsg = "Please, enter nickname. Use latin letters and digits."
    var tryagain = "Registration was unsoccessful, try again (maybe try different name)."
    var regform = document.forms["regform"];
    var nickname = regform.nickname.value;
    if (nickname == "") {
        regform.reset()
        document.getElementById("approvement").innerHTML = emptynickmsg;
    }
    else {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if(this.readyState == 4 && this.status == 204) {
                document.getElementById("approvement").innerHTML = approvemsg;
                regform.style.display = "none";
            }
            else {
                document.getElementById("approvement").innerHTML = tryagain;
                regform.reset()
            }
        };
        xhttp.open("POST", "register", true);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.send(`name=${nickname}`);
    }
}

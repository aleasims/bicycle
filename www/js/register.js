function submitNickname(){
    var approvemsg = "You are logged in.";
    var emptynickmsg = "Please, enter nickname. Use latin letters and digits."
    var regform = document.forms["regform"];
    var nickname = regform.nickname.value;
    if (nickname == "") {
        regform.reset()
        document.getElementById("approvement").innerHTML = emptynickmsg;
    }
    else {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if(this.readyState == 4 && this.status == 200) {
                document.getElementById("approvement").innerHTML = approvemsg;
                regform.style.display = "none";
            }
        };
        xhttp.open("POST", "register", true);
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.send(`name=${nickname}`);
    }
}

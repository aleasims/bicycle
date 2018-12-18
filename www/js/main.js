var dependentElements = [
    {id: "newAccButton",     case: {true: displayNone, false: styleDefault}},
    {id: "logformContainer", case: {true: displayNone, false: styleDefault}},
    {id: "logOutButton",     case: {true: styleDefault, false: displayNone}},
    {id: "accImg",           case: {true: styleDefault, false: displayNone}},
    {id: "chatButton",       case: {true: styleDefault, false: displayNone}},
    {id: "chatReference",    case: {true: styleDefault, false: displayNone}},
    {id: "chatMain",         case: {true: styleDefault, false: displayNone}}
];

function displayNone(elem) {
    elem.style.display = "none";
}

function styleDefault(elem) {
    elem.style.left = null;
}

function controlElements(selector) {
    var len = dependentElements.length;
    for (var i = 0; i < len; i++) {
        var elem = document.getElementById(dependentElements[i].id);
        if (elem !== null) {
            dependentElements[i].case[selector](elem);
        }
    }
}

function displaySwitch(selector, elem, state_true, state_false) {
    if (elem == null) {
        return;
    }
    if (selector) {
        elem.style.display = state_true;
    } else {
        elem.style.display = state_false;
    }
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires;
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function eraseCookie(name) {
    document.cookie = name + "=0; expires=Thu, 18 Dec 1999 12:00:00 UTC";
}

function clearOnlineList() {
    var list = document.getElementById("leftChatSectionContainerSupp");
    var l = list.length;
    for (var i = list.children.length - 1; i >= 0; i--) {
        list.removeChild(list.children[i]);
    }
}

function addOnlineList(elem) {
    var list = document.getElementById("leftChatSectionContainerSupp");
    list.appendChild(elem);
}

function reloadOnlineList(list) {
    clearOnlineList();
    for (var i = list.length - 1; i >= 0; i--) {
        var elem = document.createElement("div");
        elem.id = "userField_" + list[i]["uid"].toString();
        elem.setAttribute("class", "onlineUserField");
        elem.setAttribute("onclick", `requestChannel(${list[i]["uid"]});`);
        elem.innerHTML = list[i]["name"];
        addOnlineList(elem);
    }
}

function setWaitingStatus() {
    var chatEmpty = document.getElementById("chatEmptyMsg");
    chatEmpty.innerHTML = "Waiting...";
}

function setEmptyStatus() {
    var chatEmpty = document.getElementById("chatEmptyMsg");
    chatEmpty.innerHTML = "First create channel with user";
}

function createUserChat(name) {
    var chatEmpty = document.getElementById("chatEmptyMsg");
    chatEmpty.style.display = "none";
    insertChatHead(name);
}

function insertChatHead(name) {
    var container = document.getElementById("messagesContainer");
    var elem = document.createElement("div");
    elem.id = "rightChatSectionHeader";
    elem.innerHTML = name;
    container.appendChild(elem)
}
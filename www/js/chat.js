function requestChannel(target_id) {
    setWaitingStatus();
    var api = new XMLHttpRequest();
    api.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var response = JSON.parse(this.responseText);
                var answer = response.answer;
                if (answer === "timeout") {
                    alert("User is sleeping zzzz...");
                    setEmptyStatus();
                }
                else if (answer === "dismissed") {
                    alert("User does not wants to talk");
                    setEmptyStatus();
                }
                else if (answer === "accepted") {
                    var channel = response.channel;
                    createUserChat(channel['target']['name']);
                }
                else {
                    setEmptyStatus();
                }
            }
        }
    }
    api.open("GET", `/app/chat?action=request&uid=${target_id}`, true);
    api.send();
}
function sendMessage() {
	alert("msg send");
}

function updateOnlineUsers(delay) {
    var api = new XMLHttpRequest();
    api.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            online = JSON.parse(this.responseText).online;
            reloadOnlineList(online);
            setTimeout(updateOnlineUsers, delay, delay);
        }
    }
    api.open("GET", "/app/chat?action=getonlineusr", true);
    api.send();
}

function acceptChannelRequest(delay) {
    var api = new XMLHttpRequest();
    api.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var accepted = JSON.parse(this.responseText).accepted;
                if (accepted.length != 0) {
                    for (var i = accepted.length - 1; i >= 0; i--) {
                        agree = confirm(`${accepted[i]['initiator']['name']} wants to chat with you! Go chat?`)
                        if (agree) {
                            proveChannel(accepted[i]);
                        }
                        else {
                            dismissChannel(accepted[i]['chid']);
                        }
                    }
                }
                setTimeout(acceptChannelRequest, delay, delay);
            }
        }
    }
    api.open("GET", "/app/chat?action=accept", true);
    api.send();
}

function dismissChannel(chid) {
    var api = new XMLHttpRequest();
    api.onreadystatechange = function() {
        if (this.readyState == 4) {
        }
    }
    api.open("GET", `/app/chat?action=dismiss&chid=${chid}`, true);
    api.send();
}

function proveChannel(channel) {
    var api = new XMLHttpRequest();
    api.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            createUserChat(channel["initiator"]["name"]);
        }
    }
    api.open("GET", `/app/chat?action=prove&chid=${channel['chid']}`, true);
    api.send();
}

function requestChannel() {
    alert("channel requested");
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

function acceptChannelRequest() {
    var api = new XMLHttpRequest();
    api.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var accepted = JSON.parse(this.responseText).accepted;
                if (accepted.length != 0) {
                    console.log(accepted);
                    for (var i = accepted.length - 1; i >= 0; i--) {
                        if (confirm(`${accepted[i]['users'][0]['name']} wants to chat with you! Go chat?`)) {
                            console.log('Starting channel between')
                            console.log(accepted[i]['users'][0]['uid'])
                            console.log('and')
                            console.log(accepted[i]['users'][1]['uid'])
                        }
                        else {
                            dismissChannel();
                        }
                    }
                }
            }
            setTimeout(acceptChannelRequest, 1000);
        }
    }
    api.open("GET", "/app/chat?action=accept", true);
    api.send();
}

function dismissChannel() {
    console.log('Channel request dismissed');
}
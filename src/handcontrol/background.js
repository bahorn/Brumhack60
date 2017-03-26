prevSwipe = 0;
prevTap = 0;
prevAction = 0;
prevMove = 0;
limit = 500000;
curr_url = 'chrome://newtab';



function changeFocus(direction)
{
    chrome.windows.getLastFocused(
        {populate: true},
        function (window) {
            let a = 0;
            for (let i = 0; i < window.tabs.length; i++) {
                if (window.tabs[i].active == true) {
                    a = i;
                    break;
                }
            }
            if (direction == -1 && a == 0) {
                a = window.tabs.length-1;
            } else if (direction == 1 && a == window.tabs.length-1){
                a = 0;
            } else {
                a += direction;
            }
            let firstid = window.tabs[a].id;
            chrome.tabs.update(firstid, {selected: true});
            return;
        }
    );
}

function closeTab()
{
    chrome.tabs.query({ currentWindow: true, active: true }, function(tab) {
        chrome.tabs.remove(tab[0].id, function() {});
    });
}

function openTab()
{
    temp = curr_url;
    curr_url = 'chrome://newtab';
    chrome.tabs.create({'url': temp},
        function(tab) {});

}

function scroll(direction)
{

    chrome.tabs.query({ currentWindow: true, active: true }, function(tab) {
        chrome.tabs.executeScript(tab[0].id, {code: 'window.scroll(0, window.scrollY+'+direction*0.1+');'});
    });
}

function doCycle(y)
{
    x = Math.sign(y);
    chrome.tabs.query({ currentWindow: true, active: true }, function(tab) {
        chrome.tabs.executeScript(tab[0].id, {code: 'cycle('+x+');'});
    });
}

function main()
{
    let socket = io.connect('http://178.62.228.82:5000/');
    socket.on('connect', function() {
        socket.emit('input', {action: 'Chrome Connected!', value: 'a', 'timestamp':0});
    });
    chrome.runtime.onMessage.addListener(
        function(request, sender, sendResponse) {
            console.log(request.urlto);
            curr_url = request.urlto;
        }
    );
    socket.on('output', function(data) {
        if (data['action'] == "swipe") {
            if (data['timestamp'] >= prevAction+limit){
                let x = Math.sign(data['value']['direction'][0])
                let y = Math.sign(data['value']['direction'][2])
                changeFocus(x);
            }
            prevAction = data['timestamp'];
        }
        if (data['action'] == "keytap") {
            if (data['timestamp'] >= prevTap+limit) {
                openTab();
            }
            prevTap = data['timestamp'];
        }
        if (data['action'] == "screentap") {
            if (data['timestamp'] >= prevTap+limit) {
                closeTab();
            }
            prevTap = data['timestamp'];
        }
        if (data['action'] == "move") {
            if (data['value']['hand'] == "Left hand") {
                if (data['timestamp'] >= prevMove+10) {
                    let y = data['value']['direction'][2];
                    scroll(y);
                }
                prevMove = data['timestamp'];
            }
            if (data['value']['hand'] == "Right hand") {
                if (data['timestamp'] >= prevMove+15000) {
                    let y = data['value']['direction'][2];
                    doCycle(y);
                }
                prevMove = data['timestamp'];
            }
        }
    });            
}

main();

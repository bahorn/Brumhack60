all = [];
all_current = 0;

function cycle(x)
{
    console.log(x);
    all_current += x;
    if(all_current > all.length-1){
        all_current = 0;
    } else if(all_current < 0) {
        all_current = all.length-1;
    }
    all[all_current].focus();
    all[all_current].scrollIntoView(true);
    chrome.runtime.sendMessage({url: window.location.href, urlto: all[all_current].href}, function(response) {
        console.log(response);
    });

}

function main()
{   
    // Find all links
    let l = document.links;
    for (let i = 0; i < l.length;i++) {
        all.push(l[i]);
    }
}

document.onkeydown = function(e){
    e = e || window.event;
    var key = e.which || e.keyCode;
    if(key==65){
        cycle(-1);
    } else if(key==66) {
        cycle(1);
    }
};

main();

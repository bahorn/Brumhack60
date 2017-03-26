curr = 0;
prevSwipe = 1000;
class Fun {
    constructor(config){
        document.getElementById("slide").setAttribute("src",config['slides'][curr]);
        let socket = io.connect('http://'+document.domain+":"+location.port);
        socket.on('connect', function() {
            socket.emit('input', {action: 'I\'m connected!', value: 'a', 'timestamp':0});
        });
        socket.on('output', function(data) {
            if (data['action'] == "swipe") {
                /* do action here */
                /* leave a second between swipes */
                if (data['timestamp'] > prevSwipe+100000){
                    /* check direction */
                    console.log(curr);
		            let x = Math.sign(data['value']['direction'][0])
                    let y = Math.sign(data['value']['direction'][1])
                    if (x >= 1) {
                        console.log("RIGHT");
                        curr = curr+1;
                        if (curr >= 4) {
                            curr = 0;
                        }
                        document.getElementById("slide").setAttribute("src",config['slides'][curr]);
                    } else if (x <= 1) {
                        console.log("LEFT");
                        curr = curr-1;
                        if(curr < 0){
                            curr = 3;
                        }
                        document.getElementById("slide").setAttribute("src",config['slides'][curr]);
                    }
                }
                prevSwipe = data['timestamp'];
            }
        });
    }
}
function main()
{
    /* Get the config */
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200){
            let config = JSON.parse(xhttp.responseText);
            let a = new Fun(config);
        }
    }    
    xhttp.open("GET", "/static/slidedeck.json", true);
    xhttp.send();
}

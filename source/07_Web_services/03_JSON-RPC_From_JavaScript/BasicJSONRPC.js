function Log(msg){
window.alert(msg);
}

function RunSmallTest() {
    if(Connected == false)
        Log("Cannot RunSmallTest unless connected");
    else {
        var a = GetAValue();
        var b = GetBValue();
        Log("Calling remote method SmallTest using values a=" 
            + a + " and b=" + b);
        DataController.SmallTest({params:[a,b],
            onSuccess:function(sum){
                Log("SmallTest returned " + sum);
            },
            onException:function(errorObj){
                Log("SmallTest failed: " + errorObj.message);
            },
            onComplete:function(responseObj){
                Log("Call to SmallTest Complete");
            }
        });
        Log("Asynchronous call sent");
    }
}

function InitDataConnection() {
    Connected = false;
    // replace with your app url
    var url =  "http://domain:port_number/web2py_app_name/BasicJSONRPCData/call/jsonrpc"
    // var url = GetConnectionURL();   
    try {
        // Here we connect to the server and build 
        // the service object (important)
        DataController = new rpc.ServiceProxy(url);
        Connected = true;
    } catch(err) {
        Log("Connection Error: " + err.message);
        Connected = false;
    }
    var now = new Date();
    ConnectionCreated = now;
}

var ConnectionCreationTime = null;
var DataController = null;
var Connected = false;

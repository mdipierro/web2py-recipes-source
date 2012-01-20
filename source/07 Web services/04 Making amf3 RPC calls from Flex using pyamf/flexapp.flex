<?xml version="1.0" encoding="utf-8"?>
<mx:Application xmlns:mx="http://www.adobe.com/2006/mxml" layout="absolute">
    <mx:Script>
        <![CDATA[
            import mx.rpc.events.FaultEvent;
            import mx.rpc.events.ResultEvent;
            import mx.controls.Alert;

            private function resultHandler(
                    event:ResultEvent):void
            {
                trace(event.result.toString());
            }
            private function faultHandler(
                    event:FaultEvent):void
            {
                trace(event.fault.message);
            }
        ]]>
    </mx:Script>
    <mx:RemoteObject
        id="amfService"
        endpoint="http://127.0.0.1:8000/app/rpc/call/amfrpc3"
        destination="mydomain"
        showBusyCursor="true">
        <mx:method name="test" result="resultHandler(event)"
                    fault="faultHandler(event)"/>
    </mx:RemoteObject>
    <mx:Button x="250" y="150" label="Fire"
            click="amfService.test();"/>
</mx:Application>


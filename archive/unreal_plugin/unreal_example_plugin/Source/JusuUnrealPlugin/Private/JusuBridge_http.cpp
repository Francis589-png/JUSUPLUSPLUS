#include "JusuBridge.h"
#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"

FString FJusuBridge::CallBridgeHTTP(const FString& Url, const FString& JsonRequest)
{
    // Example: synchronous (!) HTTP call using FHttpModule -- for clarity only
    TSharedRef<IHttpRequest> Request = FHttpModule::Get().CreateRequest();
    Request->SetURL(Url);
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    Request->SetContentAsString(JsonRequest);

    FEvent* Event = FPlatformProcess::GetSynchEventFromPool(true);
    FString ResponseString = TEXT("{\"ok\": false, \"error\": \"timeout\"}");
    bool bSuccess = false;

    Request->OnProcessRequestComplete().BindLambda([&](FHttpRequestPtr Req, FHttpResponsePtr Resp, bool bOk){
        if (bOk && Resp.IsValid()) {
            ResponseString = Resp->GetContentAsString();
            bSuccess = true;
        }
        Event->Trigger();
    });

    Request->ProcessRequest();
    Event->Wait();
    FPlatformProcess::ReturnSynchEventToPool(Event);
    return ResponseString;
}

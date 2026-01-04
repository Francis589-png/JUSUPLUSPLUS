#include "JusuBridge.h"
#include "Sockets.h"
#include "SocketSubsystem.h"
#include "Networking/Public/Interfaces/IPv4/IPv4Endpoint.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

// Example synchronous TCP client using UE4 FSocket API
FString FJusuBridge::CallBridgeFSocket(const FString& Host, int32 Port, const FString& RequestJson)
{
    ISocketSubsystem* SocketSubsystem = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
    TSharedRef<FInternetAddr> Addr = SocketSubsystem->CreateInternetAddr();
    bool bIsValid;
    Addr->SetIp(*Host, bIsValid);
    Addr->SetPort(Port);

    if (!bIsValid) {
        return TEXT("{\"ok\": false, \"error\": \"invalid_host\"}");
    }

    FSocket* Socket = SocketSubsystem->CreateSocket(NAME_Stream, TEXT("JusuBridgeClient"), false);
    if (!Socket) {
        return TEXT("{\"ok\": false, \"error\": \"socket_create_failed\"}");
    }

    bool bConnected = Socket->Connect(*Addr);
    if (!bConnected) {
        Socket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);
        return TEXT("{\"ok\": false, \"error\": \"connect_failed\"}");
    }

    // Send JSON + newline (bridge is line-delimited)
    FTCHARToUTF8 Converter(*RequestJson);
    int32 Sent = 0;
    Socket->Send((const uint8*)Converter.Get(), Converter.Length(), Sent);
    // send newline
    const char nl = '\n';
    Socket->Send((const uint8*)&nl, 1, Sent);

    // Receive (simple blocking read with timeout)
    TArray<uint8> RecvBuffer;
    RecvBuffer.SetNumUninitialized(4096);
    int32 Read = 0;
    Socket->Recv(RecvBuffer.GetData(), RecvBuffer.Num(), Read);
    FString Response = FString(UTF8_TO_TCHAR((char*)RecvBuffer.GetData()));

    Socket->Close();
    ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);

    return Response;
}

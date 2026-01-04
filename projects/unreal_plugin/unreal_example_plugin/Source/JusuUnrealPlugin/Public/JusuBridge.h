#pragma once

#include "CoreMinimal.h"

class FJusuBridge
{
public:
    // Send a JSON request string to the bridge and return the JSON response string
    // This is a stub showing the expected API surface; implement TCP/HTTP call in plugin code.
    static FString CallBridge(const FString& JsonRequest);
};

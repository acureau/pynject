#include "pch.h"
#include <Windows.h>
#include <thread>
#include <string>
#include <fstream>
#include <streambuf>
#include <iterator>

HANDLE pipe;
void recieveLoop();

void runPythonCode(const char* code, const char* versionModule) {
    // Assign function pointers to C API function addresses.
    int(__cdecl *ensureGIL)() = reinterpret_cast<int(__cdecl*)()>(GetProcAddress(GetModuleHandleA(versionModule), "PyGILState_Ensure"));
    void(__cdecl *releaseGIL)(int) = reinterpret_cast<void(__cdecl*)(int)>(GetProcAddress(GetModuleHandleA(versionModule), "PyGILState_Release"));
    void(__cdecl *runString)(char*) = reinterpret_cast<void(__cdecl*)(char*)>(GetProcAddress(GetModuleHandleA(versionModule), "PyRun_SimpleString"));
    
    // Call functions to execute code string.
    int state = ensureGIL();
    runString((char*)code);
    releaseGIL(state);

    // Call the recieveLoop() function again.
    recieveLoop();
}

std::string readPath(std::string path) {
    std::ifstream stream(path);
    std::string contents((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
    return(contents);
}

void recieveLoop() {
    /*
        This function will loop wait for communication from a client pipe. It will read the
        passed path into a character array, and then pass it along with the module name into
        runPythonCode.
    */
    pipe = CreateNamedPipeA("\\\\.\\pipe\\executor", PIPE_ACCESS_INBOUND, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, MAX_PATH, MAX_PATH, 5000, NULL);

    int connected = ConnectNamedPipe(pipe, NULL);
    if (connected != 0) {
        // Read the info passed from client.
        char buffer[MAX_PATH * 2];
        DWORD bRead;
        while (ReadFile(pipe, buffer, sizeof(buffer), &bRead, NULL) != FALSE) {
            buffer[bRead] = '\0';
        }

        // Conver the buffer to a string and split at delimiter.
        std::string message(buffer);
        std::string path = message.substr(0, message.find("|"));
        std::string ver = message.substr((message.find("|") + 1), (message.size() - 1));
        
        // Read path into string. Close pipe, and execute code.
        std::string codeString = readPath(path);
        CloseHandle(pipe);
        runPythonCode(codeString.c_str(), ver.c_str());
    }
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved)
{
    HANDLE pipeHandle;

    switch (reason)
    {
    case DLL_PROCESS_ATTACH:
        CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)recieveLoop, hModule, 0, NULL);
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}


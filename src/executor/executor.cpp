#include "pch.h"
#include "executor.h"
#include <Windows.h>
#include <thread>
#include <string>
#include <fstream>
#include <streambuf>
#include <iterator>

void Executor::executePythonCodeString(const char* code, const char* moduleName) {
    // Assign function pointers to C API function addresses.
    int(__cdecl * ensureGIL)() = reinterpret_cast<int(__cdecl*)()>(GetProcAddress(GetModuleHandleA(moduleName), "PyGILState_Ensure"));
    void(__cdecl * releaseGIL)(int) = reinterpret_cast<void(__cdecl*)(int)>(GetProcAddress(GetModuleHandleA(moduleName), "PyGILState_Release"));
    void(__cdecl * runString)(char*) = reinterpret_cast<void(__cdecl*)(char*)>(GetProcAddress(GetModuleHandleA(moduleName), "PyRun_SimpleString"));

    // Call functions to execute code string.
    int state = ensureGIL();
    runString((char*)code);
    releaseGIL(state);

    readNamedPipeClient();
}

std::string Executor::getStringFromPath(std::string path) {
    std::ifstream stream(path);
    std::string contents((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
    return(contents);
}

/*
    This function will wait for communication from a client pipe. It will read the
    passed file scriptPath into a character array, and then pass it along with the module 
    name into executePythonCodeString.
*/
void Executor::readNamedPipeClient() {
    pipe = CreateNamedPipeA(
        "\\\\.\\pipe\\executor",
        PIPE_ACCESS_INBOUND,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
        PIPE_UNLIMITED_INSTANCES,
        MAX_PATH,
        MAX_PATH,
        5000,
        NULL
    );

    int connected = ConnectNamedPipe(pipe, NULL);
    if (connected != 0) {
        // Read the info passed from client. Length determined by [Max script path + max module name + delimiter].
        char rawPipeData[(MAX_PATH * 2) + 1];
        DWORD bytesRead;
        while (ReadFile(pipe, rawPipeData, sizeof(rawPipeData), &bytesRead, NULL) != FALSE) {
            rawPipeData[bytesRead] = '\0';
        }

        // Pipe data is passed in the format 'SCRIPT_PATH|MODULE_NAME'.
        std::string pipeData(rawPipeData);
        std::string scriptPath = pipeData.substr(0, pipeData.find("|"));
        std::string moduleName = pipeData.substr((pipeData.find("|") + 1), (pipeData.size() - 1));

        std::string codeString = getStringFromPath(scriptPath);
        CloseHandle(pipe);
        executePythonCodeString(codeString.c_str(), moduleName.c_str());
    }
}

void init() {
    Executor e;
    e.readNamedPipeClient();
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID lpReserved)
{
    switch (reason)
    {
    case DLL_PROCESS_ATTACH:
        CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)init, hModule, 0, NULL);
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
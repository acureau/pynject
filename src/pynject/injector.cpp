#include <Windows.h>
#include <iostream>
#include <psapi.h>
#include <string>
#include "injector.h"

std::string getExeRoot()
{
	char buffer[MAX_PATH];
	GetModuleFileNameA(NULL, buffer, MAX_PATH);
	std::string::size_type pos = std::string(buffer).find_last_of("\\/");
	return std::string(buffer).substr(0, pos);
}

bool checkDll(int pid) {
	// Open handle to process.
	bool found = false;
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
	if (hProcess == NULL) { return(found); }

	// Grab process modules.
	HMODULE moduleArray[1024];
	DWORD moduleArraySize;
	if (EnumProcessModules(hProcess, moduleArray, sizeof(moduleArray), &moduleArraySize)) {
		DWORD moduleCount = (moduleArraySize / sizeof(HMODULE));
		for (DWORD i = 0; i < moduleCount; i++) {
			TCHAR moduleBase[MAX_PATH];
			if (GetModuleBaseName(hProcess, moduleArray[i], moduleBase, sizeof(moduleBase))) {
				// Convert module name to string.
				std::wstring wideModule(moduleBase);
				std::string stringModule(wideModule.begin(), wideModule.end());

				// If module name is equal to 'executor.dll' then set found to true.
				if (strcmp(stringModule.c_str(), "executor.dll") == 0) {
					found = true;
				}
			}
			else { return(found); }
		}
	}
	else { return(found); }

	// Close handle to process.
	CloseHandle(hProcess);
	return(found);
}

int injectDll(int pid) {
	// Get full path to executor dll.
	std::string path = getExeRoot();
	path = path + "\\executor.dll";
	
	// Inject DLL. (Native)
	/*
		A handle to the process is opened, and memory is allocated to store the DLL's path.
		The path is then written to the process, and loaded via a remote thread which executes LoadLibraryA(path).
		We get the address of this function from our own process, because kernel32.dll is loaded at the same address across processes.
	*/
	HANDLE pyProcess = OpenProcess(PROCESS_ALL_ACCESS, false, (DWORD)pid);
	LPVOID dllMemAddr = VirtualAllocEx(pyProcess, NULL, (strlen(path.c_str()) + 1), MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	if (dllMemAddr != NULL) {
		BOOL dllWritten = WriteProcessMemory(pyProcess, dllMemAddr, path.c_str(), strlen(path.c_str()), NULL);
		if (dllWritten) {
			LPVOID loadLib = (LPVOID)GetProcAddress(GetModuleHandle(L"kernel32.dll"), "LoadLibraryA");
			if (loadLib != NULL) {
				HANDLE remoteThread = CreateRemoteThread(pyProcess, NULL, NULL, (LPTHREAD_START_ROUTINE)loadLib, dllMemAddr, NULL, NULL);
				if (remoteThread == NULL) {
					return(4);
				}
			}
			else { return(3); }
		}
		else { return(2); }
	}
	else { return(1); }
	CloseHandle(pyProcess);
	return(0);
}

int pipeMessage(const char* codePath, const char* versionModule) {
	// Wait for pipe to exist.
	int wait = 0;
	while (wait == 0) {
		wait = WaitNamedPipeA("\\\\.\\pipe\\executor", 5000);
	}
	if (wait != 0) {
		HANDLE pipeHandle = CreateFileA("\\\\.\\pipe\\executor", GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
		std::string message(codePath);
		message = message + "|" + versionModule;
		const char *cMessage = message.c_str();
		DWORD cbWritten;
		
		int writeStatus = WriteFile(pipeHandle, cMessage, strlen(cMessage) + 1, &cbWritten, NULL);
		if (! writeStatus) {
			return(1);
		}
		CloseHandle(pipeHandle);
	}
	return(0);
}

void injector::injectCode(int pid, const char* codePath, const char* versionModule) {
	// Check for DLL, if not found inject DLL.
	if (!checkDll(pid)) {
		int injCode = injectDll(pid);
		if (injCode != 0) {
			std::cout << "DLL injection failed. Error code " << injCode << "." << std::endl;
			return;
		}
	}

	// Pass strings to DLL.
	int pipeCode = pipeMessage(codePath, versionModule);
	if (pipeCode != 0) {
		std::cout << "Communication with DLL failed. Error code " << pipeCode << "." << std::endl;
		return;
	}
}
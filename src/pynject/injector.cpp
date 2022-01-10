#include <Windows.h>
#include <iostream>
#include <psapi.h>
#include <string>
#include "injector.h"

std::string injector::getExeRoot() {
	char buffer[MAX_PATH];
	GetModuleFileNameA(NULL, buffer, MAX_PATH);
	std::string::size_type pos = std::string(buffer).find_last_of("\\/");
	return std::string(buffer).substr(0, pos);
}

bool injector::isDllInjected(int pid) {
	bool found = false;
	HANDLE processHandle = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
	if (processHandle == NULL) { return(found); }

	HMODULE moduleArray[1024];
	DWORD moduleArraySize;
	if (EnumProcessModules(processHandle, moduleArray, sizeof(moduleArray), &moduleArraySize)) {
		DWORD moduleCount = (moduleArraySize / sizeof(HMODULE));
		for (DWORD i = 0; i < moduleCount; i++) {
			TCHAR moduleBase[MAX_PATH];
			if (GetModuleBaseName(processHandle, moduleArray[i], moduleBase, sizeof(moduleBase))) {

				std::wstring wstringModuleName(moduleBase);
				std::string stringModuleName(wstringModuleName.begin(), wstringModuleName.end());

				if (strcmp(stringModuleName.c_str(), "executor.dll") == 0) {
					found = true;
				}
			}
			else { return(found); }
		}
	}
	else { return(found); }

	CloseHandle(processHandle);
	return(found);
}

int injector::injectDll(int pid) {
	std::string path = getExeRoot();
	path = path + "\\executor.dll";
	
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

int injector::writeNamedPipe(const char* scriptPath, const char* moduleName) {
	int wait = 0;
	while (wait == 0) {
		wait = WaitNamedPipeA("\\\\.\\pipe\\executor", 5000);
	}
	if (wait != 0) {
		HANDLE pipeHandle = CreateFileA("\\\\.\\pipe\\executor", GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
		std::string message(scriptPath);
		message = message + "|" + moduleName;
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

void injector::injectCode(int pid, const char* codePath, const char* moduleName) {
	if (!isDllInjected(pid)) {
		int injectionExitCode = injectDll(pid);
		if (injectionExitCode != 0) {
			std::cout << "DLL injection failed. Error code " << injectionExitCode << "." << std::endl;
			return;
		}
	}

	int pipeExitCode = writeNamedPipe(codePath, moduleName);
	if (pipeExitCode != 0) {
		std::cout << "Communication with DLL failed. Error code " << pipeExitCode << "." << std::endl;
		return;
	}
}
#include "scanner.h"
#include <Windows.h>
#include <psapi.h>
#include <tchar.h>
#include <vector>
#include <iostream>

// Structure for found python processes.
struct pyProcess {
	std::string baseModule;
	std::string versionModule;
	int pid;
};

// Find version module in python process.
pyProcess checkPyProcess(int pid) {
	pyProcess proc;

	// Open handle to process.
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
	if (hProcess == NULL) { return(proc); }

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

				// If both 'python' and 'dll' are in the string.
				if ((stringModule.find("python") != std::string::npos) && (stringModule.find("dll") != std::string::npos)) {

					// Get process base module name.
					TCHAR baseModule[MAX_PATH];
					GetModuleBaseName(hProcess, 0, baseModule, sizeof(baseModule));
					std::wstring wideBase(baseModule);
					std::string stringBase(wideBase.begin(), wideBase.end());

					// Create pyProcess and append to list.
					proc.pid = pid;
					proc.versionModule = stringModule;
					proc.baseModule = stringBase;
				}
			}
			else { return(proc); }
		}
	}
	else { return(proc); }

	// Close handle to process.
	CloseHandle(hProcess);
	return(proc);
}

// Find all python processes, create a pyProcess for each, and return them in a vector.
std::vector<pyProcess> findPythonProcesses() {
	// Grab all processes' IDs.
	std::vector<pyProcess> procList;
	DWORD pidArray[1024];
	DWORD pidArraySize;
	DWORD processCount;
	if (!EnumProcesses(pidArray, sizeof(pidArray), &pidArraySize)) { return(procList); }
	processCount = (pidArraySize / sizeof(DWORD));

	// Loop through processes and check modules.
	for (DWORD i = 0; i < processCount; i++) {
		pyProcess proc = checkPyProcess(pidArray[i]);

		if (!proc.versionModule.empty()) {
			procList.push_back(proc);
		}
	}

	return(procList);
}

// Direct the flow of the scanner.
void scanner::scan() {
	if (processId == 0) {
		std::vector<pyProcess> procList = findPythonProcesses();
		if (!procList.empty()) {
			// Print python processes.
			std::cout << "Python Processes" << std::endl << "================" << std::endl;
			for (int i = 0; i < procList.size(); i++) {
				std::cout << "  Base: " << procList[i].baseModule << " | ";
				std::cout << "Version: " << procList[i].versionModule << " | ";
				std::cout << "PID: " << procList[i].pid << std::endl;
			}
		}
		else { std::cout << "No python processes found." << std::endl; }
	}
	else {
		pyProcess proc = checkPyProcess(processId);
		if (!proc.versionModule.empty()) {
			versionModule = proc.versionModule;
			found = true;
		} else { std::cout << "Invalid PID or non-python process." << std::endl; }
	}
}
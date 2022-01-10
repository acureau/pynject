#include "scanner.h"
#include <Windows.h>
#include <psapi.h>
#include <tchar.h>
#include <vector>
#include <iostream>

struct pyProcess {
	std::string baseModule;
	std::string moduleName;
	int pid;
};

pyProcess isPythonProcess(int pid) {
	pyProcess proc;

	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
	if (hProcess == NULL) { 
		return(proc); 
	}

	HMODULE moduleArray[1024];
	DWORD moduleArraySize;
	if (EnumProcessModules(hProcess, moduleArray, sizeof(moduleArray), &moduleArraySize)) {
		DWORD moduleCount = (moduleArraySize / sizeof(HMODULE));
		for (DWORD i = 0; i < moduleCount; i++) {
			TCHAR moduleBase[MAX_PATH];
			if (GetModuleBaseName(hProcess, moduleArray[i], moduleBase, sizeof(moduleBase))) {

				std::wstring wideModule(moduleBase);
				std::string stringModule(wideModule.begin(), wideModule.end());

				if ((stringModule.find("python") != std::string::npos) && (stringModule.find("dll") != std::string::npos)) {

					TCHAR baseModule[MAX_PATH];
					GetModuleBaseName(hProcess, 0, baseModule, sizeof(baseModule));
					std::wstring wideBase(baseModule);
					std::string stringBase(wideBase.begin(), wideBase.end());

					proc.pid = pid;
					proc.moduleName = stringModule;
					proc.baseModule = stringBase;
				}
			}
			else { 
				return(proc); 
			}
		}
	}
	else { 
		return(proc); 
	}

	CloseHandle(hProcess);
	return(proc);
}

std::vector<pyProcess> getPythonProcesses() {
	std::vector<pyProcess> procList;
	DWORD pidArray[1024];
	DWORD pidArraySize;
	DWORD processCount;
	if (!EnumProcesses(pidArray, sizeof(pidArray), &pidArraySize)) { return(procList); }
	processCount = (pidArraySize / sizeof(DWORD));

	for (DWORD i = 0; i < processCount; i++) {
		pyProcess proc = isPythonProcess(pidArray[i]);

		if (!proc.moduleName.empty()) {
			procList.push_back(proc);
		}
	}

	return(procList);
}

void scanner::scan() {
	if (processId == 0) {
		std::vector<pyProcess> procList = getPythonProcesses();
		if (!procList.empty()) {
			std::cout << "Python Processes" << std::endl << "================" << std::endl;
			for (int i = 0; i < procList.size(); i++) {
				std::cout << "  Base: " << procList[i].baseModule << " | ";
				std::cout << "Version: " << procList[i].moduleName << " | ";
				std::cout << "PID: " << procList[i].pid << std::endl;
			}
		}
		else { 
			std::cout << "No python processes found." << std::endl; 
		}
	}
	else {
		pyProcess proc = isPythonProcess(processId);
		if (!proc.moduleName.empty()) {
			moduleName = proc.moduleName;
			found = true;
		} 
		else { 
			std::cout << "Invalid PID or non-python process." << std::endl; 
		}
	}
}
#include <Windows.h>
#include <iostream>
#include <string>
#include <fstream>
#include "scanner.h"
#include "injector.h"

void printUsage() {
	std::cout << "Usage" << std::endl << "=====" << std::endl;
	std::cout << "  pynject scan" << std::endl;
	std::cout << "  pynject <PID> script.py" << std::endl;
}

std::string getFullPath(const char* codePath) {
	char fullPath[MAX_PATH];
	GetFullPathNameA(codePath, sizeof(fullPath), fullPath, NULL);
	std::ifstream checkfile(fullPath);
	if (checkfile.good()) {
		std::string path(fullPath);
		return(path);
	}
	else {
		return("error");
	}
}

int main(int argc, char *argv[]) {
	// Incorrect argument amount.
	if (argc > 3 || argc < 2) {
		printUsage();
	}
	else {
		if (!strcmp(argv[1], "scan")) {
			scanner scnr;
			scnr.scan();
		}
		else if (atoi(argv[1]) != 0) {
			if (argc == 3) {
				scanner scnr(atoi(argv[1]));
				scnr.scan();
				if (scnr.found) {
					injector inj;
					std::string fullCodePath = getFullPath(argv[2]);
					if (fullCodePath.compare("error") == 0) {
						std::cout << "Invalid script path." << std::endl;
						return(0);
					}
					inj.injectCode(scnr.processId, fullCodePath.c_str(), (scnr.versionModule).c_str());
				}
			}
			else { printUsage(); }
		}
		else { printUsage(); }
	}
}
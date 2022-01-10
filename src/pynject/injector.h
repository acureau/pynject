#pragma once
#include <string>

class injector
{
public:

	std::string getExeRoot();
	bool isDllInjected(int pid);
	void injectCode(int pid, const char *codePath, const char *moduleName);
	int injectDll(int pid);
	int writeNamedPipe(const char* codePath, const char* moduleName);
};


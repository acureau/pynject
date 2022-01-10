#pragma once
#include <string>
#include <Windows.h>

class Executor {
	public:
		HANDLE pipe;

		void readNamedPipeClient();
		void executePythonCodeString(const char* code, const char* moduleName);
		std::string getStringFromPath(std::string path);
};
#pragma once
#include <Windows.h>
#include <string>

class scanner
{
public:
	std::string versionModule;
	int processId = 0;
	bool found = false;

	void scan();

	scanner() {
	}
	scanner(int pid) {
		processId = pid;
	}

private:
};


//main file for simulation

//G4 built in files we want to include
#include "G4UImanager.hh"
#include "G4UIExecutive.hh"
#include "G4RunManagerFactory.hh" 
#include "G4VisExecutive.hh"
#include"G4SteppingVerbose.hh"

//our files in the include folder
#include "DetectorConstruction.hh"
#include "PhysicsList.hh"
#include "ActionInitialization.hh"

using namespace BremSim;

// for printing (debugging)
#include <iostream>
using namespace std;

int main(int argc, char** argv)
{
	// initialize (or don't) a UI
	G4UIExecutive* ui = nullptr; 
	if (argc == 1) 
	{ 
		ui = new G4UIExecutive(argc, argv);
	}

	// create run manager
	auto* runManager = G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

	//Set mandatory user intialization classes
	runManager->SetUserInitialization(new DetectorConstruction());
	runManager->SetUserInitialization(new PhysicsList());
	runManager->SetUserInitialization(new ActionInitialization());

	//Initialize visualization
	G4VisManager* visManager = new G4VisExecutive;
	visManager->Initialize();

	// random seed
	long seed = 42; //meaning of life
	CLHEP::HepRandom::setTheSeed(seed);
	G4Random::setTheSeed(seed);

	
	//Start the UI
	G4UImanager* UImanager = G4UImanager::GetUIpointer();


	if (!ui) //batch mode
	{
		G4String command = "/control/execute ";
		G4String fileName = argv[1];
		UImanager->ApplyCommand(command + fileName);
	}
	else //interactive mode
	{
		UImanager->ApplyCommand("/control/execute macros/init_vis.mac");
		ui->SessionStart();
		delete ui;
	}

	//job termination
	delete visManager;
	delete runManager;

	return 0;
}
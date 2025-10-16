//main file for simulation

//G4 built in files we want to include
#include "G4RunManagerFactory.hh" 
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"

//our files in the include folder
#include "DetectorConstruction.hh"
#include "PhysicsList.hh"
#include "ActionInitialization.hh"

int main(int argc, char** argv)
{
	G4UIExecutive* ui = nullptr; //pointer to GRUIExecutive class initialized to nullptr
	if (argc == 1) //if no command line arguments are made, run in interactive mode
	{ 
		ui = new G4UIExecutive(argc, argv); //GRUIExecutive object, passing comand line arguments to it initializing G4 UI session
	}

	auto* runManager = G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);

	//Set mandatory user intialization classes
	runManager->SetUserInitialization(new DetectorConstruction());
	runManager->SetUserInitialization(new PhysicsList());
	runManager->SetUserInitialization(new ActionInitialization());

	//Initialize visualization
	G4VisManager* visManager = new G4VisExecutive;
	visManager->Initialize();
	G4UImanager* UImanager = G4UImanager::GetUIpointer();

	if (!ui) //batch mode
	{
		G4String command = "/control/execute ";
		G4String fileName = argv[1];
		UImanager->ApplyCommand(command + fileName);
	}
	else //interactive mode
	{
		UImanager->ApplyCommand("/control/exetue ./macros/init_vis.mac");
		ui->SessionStart();
		delete ui;
	}

	delete visManager;
	delete runManager;
	return 0;

}
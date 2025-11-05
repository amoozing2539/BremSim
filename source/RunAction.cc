#include "RunAction.hh"
#include "G4ThreeVector.hh"
#include "G4UunitsTable.hh"

namespace BremSim
{
	RunAction::RunAction()
	{
		// set up analysis nTuples and output files

		auto analysisManager = G4AnalysisManager::Instance();

		// set default settings
		analysisManager->SetDefaultFileType("root");
		analysisManager->SetNTupleMerging(true);
		analysisManager->SetVerboseLevel(1);
		analysisManager->SetFileName("output")

		// create nTuple to store the absolute energies
		const G4int ntupleID1 = analysisManager->CreateNtuple("Absolute Energies", "Gamma Energies");
	}
}







// #include "G4Run.hh"
// #include "G4RunManager.hh"
// #include "G4AnalysisManager.hh"
// #include "G4SystemOfUnits.hh"


// RunAction::RunAction() : G4UserRunAction()
// {
// 	// Create a G4AnalysisManager instance
// 	auto analysisManager = G4AnalysisManager::Instance();
// 	analysisManager->SetVerboseLevel(1);
// 	analysisManager->SetNtupleMerging(true);

// 	// Create an n-tuple (like a table) to store our data
// 	analysisManager->CreateNtuple("BremHits", "Bremsstrahlung Hits");
// 	analysisManager->CreateNtupleIColumn("EventID");				// Col 0: Event Number
// 	analysisManager->CreateNtupleIColumn("ParticleID");				// Col 1: Particle type
// 	analysisManager->CreateNtupleDColumn("Energy_keV");				// Col 2: Energy in keV. Saving them as doubles bc our data will be doubles. 
// 	analysisManager->CreateNtupleDColumn("PosX_mm");				// Col 3: X position (mm)
// 	analysisManager->CreateNtupleDColumn("PosY_mm");				// Col 4: Y position (mm)
// 	analysisManager->CreateNtupleDColumn("MomDirX");				// Col 5: Momentum Direction X
// 	analysisManager->CreateNtupleDColumn("MomDirY");				// Col 6: Momentum Direction Y
// 	analysisManager->CreateNtupleDColumn("MomDirZ");				// Col 7: Momentum Direction Z
// 	analysisManager->FinishNtuple();
// }


// void RunAction::BeginOfRunAction(const G4Run* /*run*/)
// {
// 	// Get analysis manager
// 	auto analysisManager = G4AnalysisManager::Instance();

// 	// open output file
// 	G4String fileName = "output.csv";
// 	analysisManager->OpenFile(fileName);
// 	G4cout << "using " << analysisManager->GetType() << G4endl;
// }


// void RunAction::EndOfRunAction(const G4Run* /*run*/)
// {
// 	// Get analysis manager
// 	auto analysisManager = G4AnalysisManager::Instance();

// 	// Save ntuple
// 	analysisManager->Write();
// 	analysisManager->CloseFile();
}
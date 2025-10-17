#include "RunAction.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4AnalysisManager.hh"
#include "G4SystemOfUnits.hh"

RunAction::RunAction() : G4UserRunAction()
{
	// Create a G4AnalysisManager instance
	auto analysisManager = G4AnalysisManager::Instance();
	analysisManager->SetVerboseLevel(1);
	analysisManager->SetNtupleMerging(true);

	// Create an n-tuple (like a table) to store our data
	analysisManager->CreateNtuple("BremHits", "Bremsstrahlung Hits");
	analysisManager->CreateNtupleIColumn("EventID");				// Col 0: Event Number
	analysisManager->CreateNtupleIColumn("ParticleID");				// Col 1: Particle type
	analysisManager->CreateNtupleIColumn("Energy_keV");				// Col 2: Energy in keV
	analysisManager->CreateNtupleIColumn("PosX_mm");				// Col 3: X position (mm)
	analysisManager->CreateNtupleIColumn("PosY_mm");				// Col 4: Y position (mm)
	analysisManager->CreateNtupleIColumn("MomDirX");				// Col 5: Momentum Direction X
	analysisManager->CreateNtupleIColumn("MomDirY");				// Col 6: Momentum Direction Y
	analysisManager->CreateNtupleIColumn("MomDirZ");				// Col 7: Momentum Direction Z
	analysisManager->FinishNtuple();
}

RunAction::~RunAction() {}

// write analysisManager into .csv file
void RunAction::BeginOfRunAction(const G4Run* run)
{
	// Get analysis manager
	auto analysisManager = G4AnalysisManager::Instance();

	// open output file
	G4String fileName = "output.csv";
	analysisManager->OpenFile(fileName);
}

void RunAction::EndOfRunAction(const G4Run* run)
{
	// Get analysis manager
	auto analysisManager = G4AnalysisManager::Instance();

	// Write and close the file
	analysisManager->Write();
	analysisManager->CloseFile();
}
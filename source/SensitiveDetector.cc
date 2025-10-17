// Data collection (our detector made of air)
// for now we will just print the data to verify it works

#include "SensitiveDetector.hh"
#include "G4Step.hh"
#include "G4TouchableHistory.hh"
#include "G4SystemOfUnits.hh"
#include "G4UnitsTable.hh"
#include "G4AnalysisManager.hh"

SensitiveDetector::SensitiveDetector(G4String name) : G4VSensitiveDetector(name) {}
SensitiveDetector::~SensitiveDetector() {}

G4bool SensitiveDetector::ProcessHits(G4Step* aStep, G4TouchableHistory* RoHist)
{
	// Get the particle's track
	auto track = aStep->GetTrack();

	// only interested in particles just entering the detector volume 
	if (aStep->GetPreStepPoint()->GetStepStatus() != fGeomBoundary)
	{
		return false;
	}

	// Get data from the step
	G4int eventID = G4RunManager::GetRunManger()->GetCurrentEvent()->GetEventID();
	G4int particleID = track->GetDefinition()->GetPDGEncoding();
	G4double energy = aStep->GetPreStepPoint()->GetKineticEnergy() / keV;
	G4ThreeVector pos = aStep->GetPreStepPoint()->GetPosition() / mm;
	G4ThreeVector momentumDir = aStep->GetPreStepPoint()->GetMomentumDirection();

	// Get the analysis manager and fill the n-tuple
	auto analysisManager = G4AnalysisManager::Instance();
	analysisManager->FillNtupleIColumn(0, eventID);
	analysisManager->FillNtupleIColumn(1, particleID);
	analysisManager->FillNtupleIColumn(2, energy);
	analysisManager->FillNtupleIColumn(3, pos.x());
	analysisManager->FillNtupleIColumn(4, pos.y());
	analysisManager->FillNtupleIColumn(5, momentumDir.x());
	analysisManager->FillNtupleIColumn(6, momentumDir.y());
	analysisManager->FillNtupleIColumn(7, momentumDir.z());
	analysisManager->AddNtupleRow();

	return true;

	///--------------OLD CODE----------------------//
	// get relevant info
	//G4String particleName = track->GetDefinition()->GetParticleName();
	//G4double energy = aStep->GetPreStepPoint()->GetKineticEnergy();
	//G4ThreeVector pos = aStep->GetPreStepPoint()->GetPosition();
	//G4ThreeVector momentumDir = aStep->GetPreStepPoint()->GetMomentumDirection();

	//// Print the data to the console (just to see if it works for now)
	//G4cout << "Hit >>> Particle: " << particleName
	//	   << ", Energy: " << G4BestUnit(energy, "Energy")
	//	   << ", Position: " << G4BestUnit(pos, "Length")
	//	   << ", Momentum Direction: " << momentumDir
	//	   << G4endl;
	// return true
}
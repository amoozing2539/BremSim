// Data collection (our detector made of air)
// for now we will just print the data to verify it works

#include "SensitiveDetector.hh"
#include "G4Step.hh"
#include "G4TouchableHistory.hh"
#include "G4SystemOfUnits.hh"
#include "G4UnitsTable.hh"

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

	// get relevant info
	G4String particleName = track->GetDefinition()->GetParticleName();
	G4double energy = aStep->GetPreStepPoint()->GetKineticEnergy();
	G4ThreeVector pos = aStep->GetPreStepPoint()->GetPosition();
	G4ThreeVector momentumDir = aStep->GetPreStepPoint()->GetMomentumDirection();

	// Print the data to the console (just to see if it works for now)
	G4cout << "Hit >>> Particle: " << particleName
		   << ", Energy: " << G4BestUnit(energy, "Energy")
		   << ", Position: " << G4BestUnit(pos, "Length")
		   << ", Momentum Direction: " << momentumDir
		   << G4endl;

	return true;
}
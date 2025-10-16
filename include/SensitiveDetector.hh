// Data Collection (our detector) 

#ifndef SENSITIVEDETECTOR_HH
#define SENSITIVEDETECTOR_HH

#include "G4VSensitiveDetector.hh"

class SensitiveDetector : public G4VSensitiveDetector
{
public: 
	SensitiveDetector(G4String name);
	~SensitiveDetector();

protected:
	virtual G4bool ProcessHits(G4Step* aStep, G4TouchableHistory* ROHist);
};
#endif
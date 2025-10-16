// Particle Gun

#ifndef PRIMARYGENERATORACTION_HH
#define PRIMARYGENERATORACTION_HH

#include "G4VUserPrimaryGeneratorAction.hh"
class G4ParticleGun;
class G4Event;

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
	PrimaryGeneratorAction();
	~PrimaryGeneratorAction();
	virtual void GeneratePrimaries(G4Event*);

private:
	G4ParticleGun* fParticleGun;
};
#endif
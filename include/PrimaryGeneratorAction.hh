// Particle Gun

#ifndef PRIMARYGENERATORACTION_H
#define PRIMARYGENERATORACTION_H 1

#include "G4VUserPrimaryGeneratorAction.hh"
#include "G4ThreeVector.hh"
#include "globals.hh"
#include "G4SystemOfUnits.hh"
#include "G4ParticleGun.hh"


namespace BremSim
{
	class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
	{
		public:
			PrimaryGeneratorAction();
			~PrimaryGeneratorAction();

			virtual void GeneratePrimaries(G4Event*);

			G4ParticleGun* fParticleGun;
	};
}
#endif
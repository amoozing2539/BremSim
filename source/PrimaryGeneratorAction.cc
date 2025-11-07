//Particle Gun

#include "PrimaryGeneratorAction.hh"

#include "G4Event.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"

#include "Randomize.hh"

#include "G4UnitsTable.hh"


namespace BremSim
{
	PrimaryGeneratorAction::PrimaryGeneratorAction()
	{
		// set up the gun
		G4int numParticles = 1; // do one for one per action. monoenergetic particles
		fParticleGun = new G4ParticleGun(numParticles);

		// set our gun to the desired particle
		const G4String& particleName = "e-";
		G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
		G4ParticleDefinition* particle = particleTable->FindParticle(particleName);
		fParticleGun->SetParticleDefinition(particle); 									// set gun with desired particle 
		fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., 1.)); 			// shoot along the z-axis
		fParticleGun->SetParticleEnergy(5.0 * MeV); 									// Hardcode Energy of the beam and we'll change it in the mac files

	}

	
	PrimaryGeneratorAction::~PrimaryGeneratorAction(){ delete fParticleGun; }


	void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) // generate primary particles
	{
		// randomize starting position of each electron within a 1 mm diameter in the xy plane
		G4double radius = .5*mm;
		double x,y;

		// square sampling 
		do{
			x = G4UniformRand() * (2.0*radius)-radius;
			y = G4UniformRand() * (2.0*radius)-radius;
			
		} while (x*x + y*y > radius*radius); //while area stays within the circle area (normalized)

		fParticleGun->SetParticlePosition(G4ThreeVector(x,y,-5 * cm));
		fParticleGun->GeneratePrimaryVertex(event); // satisfy "generate primaries" here
	}
}

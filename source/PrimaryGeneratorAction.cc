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

		// rejection sampling loop to pick a random (x,y) point within a circle of radius r
		// rejection sampling simulates a beam spot size. 
		do{
			// sets x and y to be between -radius and radius
			x = G4UniformRand() * (2.0*radius)-radius; //G4UniformRand() returns a random number between 0 and 1.
			y = G4UniformRand() * (2.0*radius)-radius;
			
		} while (x*x + y*y > radius*radius); //Keep sampling if the point lies outside the circle (does not satisfy our criteria)

		//break down of the rejection sampling algorithm above is as follows:
		// 1. Select x from a unifrom distribution between [-R, R]
		// 2. Select y from a unifrom distribution between [-R, R]
		// 3. Accept (x,y)_i if: x^2+y^2<=R^2, else: reject (x,y)_i and sample again

		//set get position and fire particle into the world 
		fParticleGun->SetParticlePosition(G4ThreeVector(x,y,-5 * cm));
		fParticleGun->GeneratePrimaryVertex(event); // satisfy "generate primaries" here
	}
}

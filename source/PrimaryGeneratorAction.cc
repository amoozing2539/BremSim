//Particle Gun

#include "PrimaryGeneratorAction.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction() : G4VUserPrimaryGeneratorAction()
{
	fParticleGun = new G4ParticleGun(1);

	// Default particle properties
	G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
	G4ParticleDefinition* particle = particleTable->FindParticle("e-"); // electron
	fParticleGun->SetParticleDefinition(particle); // set the gun with electrons
	fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0., 0., 1.)); // shoot along the z-axis
	fParticleGun->SetParticleEnergy(5.0 * MeV); // Default Energy of the beam
	fParticleGun->SetParticlePosition(G4ThreeVector(0., 0., -5.0 * cm)); // Start 5cm IN FRONT of the foil
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
	delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{
	fParticleGun->GeneratePrimaryVertex(anEvent);
}
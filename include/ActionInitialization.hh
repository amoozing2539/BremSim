#ifndef ACTIONINITIALIZTION_HH
#define ACTIONINITIALIZTION_HH

#include "G4VUserActionInitialization.hh"

class ActionInitialization : public G4VUserActionInitialization
{
public: 
	ActionInitialization();
	~ActionInitialization();
	virtual void Build() const;
};
#endif
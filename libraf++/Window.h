/*
-------------------------------------------------------------------------
OBJECT NAME:	Window.h

FULL NAME:	Generic Shell with Form class

TYPE:		Abstract/Base

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef WINDOW_H
#define WINDOW_H

#include <Xm/Form.h>
#include <Xm/RowColumn.h>



/* -------------------------------------------------------------------- */
class WinForm {

public:
  enum winType { Form, RowColumn };

		WinForm(const Widget parent, char name[], winType wt);
  virtual	~WinForm();

  virtual void	PopUp() const;
  virtual void	PopDown() const;

  void		SetPosition(int x, int y) const;

  Widget	Shell()	 const	{ return(shell); }
  Widget	Window() const	{ return(window); }

private:
  Widget	shell, window;

};	/* END WINDOW.H */

#endif

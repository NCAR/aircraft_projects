
Notes about .ssh files here:


.ssh/authorized_keys
    This contains the public key of the aster@aster user.
    ssh man page says:
	This file is not highly sensitive, but the
        recommended permissions are read/write for the user, and not
	accessible by others.
    Therefore I will put this in the svn repository.

.ssh/id_dsa
    The private key, so this won't be checked into subversion.
.ssh/config
    Also should not be world readable, so won't check into subversion.

    

# To set the ignore property for those files:
svn propset svn:ignore "id_dsa
config" root/.ssh

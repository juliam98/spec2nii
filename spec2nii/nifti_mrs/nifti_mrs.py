import nibabel as nib
from .validator import validate_nifti_mrs

base_class = nib.nifti2.Nifti2Image


def set_nifti1():
    '''Set the base class of NIfTI_MRS to be nibabel.nifti1.Nifti1Image'''
    global base_class
    base_class = nib.nifti1.Nifti1Image


def NIfTI_MRS(*args, **kwargs):
    '''Wrapper function around NIfTI_MRS class that allows for dynamic inheritance.
    Initilise a NIfTI MRS object which can be saved to disk.
    :param dataobj: Four to seven dimensional complex numpy array.
    :param affine: None or (4,4) array-like
                    homogenous affine giving relationship between voxel coordinates and
                    world coordinates.  Affine can also be None.  In this case,
                    ``obj.affine`` also returns None, and the affine as written to disk
                    will depend on the file format.
    :param float dwelltime: Spectroscopic time-domain dwelltime in seconds.
    :param header_ext : nifti_mrs.hdr_ext object.
    :param header: None or mapping or header instance, optional
                    metadata for this image format
    :param extra: None or mapping, optional
                    metadata to associate with image that cannot be stored in the
                    metadata of this image type
    :param file_map : mapping, optional
                    mapping giving file information for this image format
    '''
    global base_class

    class NIfTI_MRS(base_class):
        """Class to contain a NIfTI MRS dataset. Derived from nibabel's Nifti2Image."""

        def __init__(self, dataobj, affine, dwelltime, header_ext, header=None, extra=None, file_map=None):
            """Initilise a NIfTI MRS object which can be saved to disk.
            :param dataobj: Four to seven dimensional complex numpy array.
            :param affine: None or (4,4) array-like
                            homogenous affine giving relationship between voxel coordinates and
                            world coordinates.  Affine can also be None.  In this case,
                            ``obj.affine`` also returns None, and the affine as written to disk
                            will depend on the file format.
            :param float dwelltime: Spectroscopic time-domain dwelltime in seconds.
            :param header_ext : nifti_mrs.hdr_ext object.
            :param header: None or mapping or header instance, optional
                            metadata for this image format
            :param extra: None or mapping, optional
                            metadata to associate with image that cannot be stored in the
                            metadata of this image type
            :param file_map : mapping, optional
                            mapping giving file information for this image format
            """
            super().__init__(dataobj, affine, header=header, extra=extra, file_map=file_map)

            # Add the header extensions
            json_s = header_ext.get_json(dimensions=dataobj.ndim)
            extension = nib.nifti1.Nifti1Extension(44, json_s.encode('UTF-8'))
            self.header.extensions.append(extension)

            # Set intent_name
            self.set_version_info(0, 2)

            # Set the dwell time of the time dimension
            self.set_dwell_time(dwelltime)

        def set_dwell_time(self, dwelltime):
            """Set dwelltime (pixdim[4])"""
            pixDim = self.header['pixdim']
            pixDim[4] = dwelltime
            self.header['pixdim'] = pixDim

        def set_version_info(self, major, minor):
            """puts mrs_v{major}_{minor} into intent_name"""
            self.header['intent_name'] = f'mrs_v{major}_{minor}'.encode()

        def validate(self):
            """Run NIfTI MRS validation."""
            validate_nifti_mrs(self)

        def save(self, filename):
            """ Utility function """
            nib.save(self, filename)

    return NIfTI_MRS(*args, **kwargs)

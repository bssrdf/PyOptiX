from pyoptix._driver import _OptixContextWrapper
from pyoptix._driver import RTbuffertype
from pyoptix.objects.commons.optix_scoped_object import OptixScopedObject
from pyoptix.compiler import OptixCompiler
from pyoptix.objects.optix_program import OptixProgram
from pyoptix.objects.optix_acceleration import OptixAcceleration
from pyoptix.objects.optix_selector import OptixSelector
from pyoptix.objects.optix_transform import OptixTransform
from pyoptix.objects.optix_geometry_group import OptixGeometryGroup
from pyoptix.objects.optix_group import OptixGroup
from pyoptix.objects.optix_geometry_instance import OptixGeometryInstance
from pyoptix.objects.optix_material import OptixMaterial
from pyoptix.objects.optix_geometry import OptixGeometry
from pyoptix.objects.optix_texture import OptixTexture
from pyoptix.objects.optix_buffer import OptixBuffer


class OptixContext(_OptixContextWrapper, OptixScopedObject):

    def __init__(self):
        _OptixContextWrapper.__init__(self)
        OptixScopedObject.__init__(self)
        self.compiler = None

    def init_compiler(self, output_path=None, include_paths=None, arch=None, use_fast_math=None):
        kwargs = {}
        if output_path:
            kwargs['output_path'] = output_path
        if include_paths:
            kwargs['include_paths'] = include_paths
        if arch:
            kwargs['arch'] = arch
        if use_fast_math:
            kwargs['use_fast_math'] = use_fast_math
        self.compiler = OptixCompiler(**kwargs)

    def create_acceleration(self, builder, traverser):
        """
        :rtype : OptixAcceleration
        """
        native = self._create_accelerator(builder, traverser)
        return OptixAcceleration(native, context=self)

    def create_buffer(self, buffer_type):
        """
        :param buffer_type
        :rtype : OptixBuffer
        """
        native_buffer_type = None
        if buffer_type == 'i':
            native_buffer_type = RTbuffertype.RT_BUFFER_INPUT
        elif buffer_type == 'o':
            native_buffer_type = RTbuffertype.RT_BUFFER_OUTPUT
        elif buffer_type == 'io':
            native_buffer_type = RTbuffertype.RT_BUFFER_INPUT_OUTPUT
        if native_buffer_type is None:
            raise ValueError("Buffer type must be 'i' 'o' or 'io'")

        native = self._create_buffer(native_buffer_type)
        return OptixBuffer(native, context=self)

    def create_buffer_from_numpy_array(self, buffer_type, numpy_array, drop_last_dim=False):
        buffer = self.create_buffer(buffer_type)
        buffer.restructure_and_copy_from_numpy_array(numpy_array, drop_last_dim)
        return buffer

    def create_texture_sampler(self):
        """
        :rtype : OptixTexture
        """
        native = self._create_texture_sampler()
        return OptixTexture(native, context=self)

    def create_geometry(self):
        """
        :rtype : OptixGeometry
        """
        native = self._create_geometry()
        return OptixGeometry(native, context=self)

    def create_material(self):
        """
        :rtype : OptixMaterial
        """
        native = self._create_material()
        return OptixMaterial(native, context=self)

    def create_geometry_instance(self):
        """
        :rtype : OptixGeometryInstance
        """
        native = self._create_geometry_instance()
        return OptixGeometryInstance(native, context=self)

    def create_group(self):
        """
        :rtype : OptixGroup
        """
        native = self._create_group()
        return OptixGroup(native, context=self)

    def create_geometry_group(self):
        """
        :rtype : OptixGeometryGroup
        """
        native = self._create_geometry_group()
        return OptixGeometryGroup(native, context=self)

    def create_transform(self):
        """
        :rtype : OptixTransform
        """
        native = self._create_transform()
        return OptixTransform(native, context=self)

    def create_selector(self):
        """
        :rtype : OptixSelector
        """
        native = self._create_selector()
        return OptixSelector(native, context=self)

    def create_program_from_file(self, file_name, function_name):
        """
        :rtype : OptixProgram
        """
        if not self.compiler:
            self.init_compiler()

        # Compile program
        compiled_file_path = self.compiler.compile(file_name)

        # Create program object from compiled file
        native = self._create_program_from_file(compiled_file_path, function_name)
        return OptixProgram(native, context=self)

    def launch(self, entry_point_index, width, height=None, depth=None):
        if not height:
            self._launch_1d(entry_point_index, width)
        elif not depth:
            self._launch_2d(entry_point_index, width, height)
        else:
            self._launch_3d(entry_point_index, width, height, depth)

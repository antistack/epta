def mapper_test():
    from dataclasses import dataclass, field

    import epta.core as ec
    import epta.tools.base as eb
    import numpy as np

    @dataclass
    class PositionMapperTest(eb.PositionMapper):
        config: field(init=True)
        _key_mappings: tuple = tuple()
        x: callable = lambda *args, **kwargs: 0
        name: str = 'PositionMapperTest'

    settings = ec.Settings()
    settings.path = 'test/path/123'
    config = ec.Config(settings)

    mapper = eb.PositionMapper(config, name='position_mapper_test')
    mapper.x = lambda cfg: len(cfg.settings.path) + np.random.randint(1, 10)

    mapper_wrapper = eb.PositionMapperWrapper(mapper)
    mapper_wrapper_2 = eb.PositionMapperWrapper(PositionMapperTest(config, name='help'))

    position_manager = ec.ToolDict(tools=[mapper_wrapper, mapper_wrapper_2])
    position_manager.update()
    return config, position_manager


def hooker_test():
    import epta.core as ec
    import epta.core.base_ops as eco
    import epta.tools.hookers.image_hookers as eti
    import numpy as np

    class CustomImageHooker(eti.BaseImageHooker, ec.PositionDependent):
        def hook_image(self, *args, **kwargs):
            return np.zeros((300, 300, 3), dtype=np.uint8)

    config, position_manager = mapper_test()

    hooker = CustomImageHooker(position_manager=position_manager, name='custom_image_hooker',
                               key='position_mapper_test')
    data_0 = hooker.use()
    stream_0 = eco.Variable(hooker)
    stream_1 = eco.Variable(hooker)
    pipeline = eco.Sequential([
        eco.Concatenate([
            stream_0, stream_1
        ])
    ])

    # data = pipeline.use()
    return pipeline, position_manager


def cropper_test():
    import epta.tools.base as eb
    import epta.core.base_ops as eco

    pipeline, position_manager = hooker_test()

    cropper_0 = eco.Variable(
        eco.Sequential([
            eco.DataReduce('image_0'),  # here result is (image, )
            eco.Atomic(key=0),  # We need to take at index 0
            eb.PositionCropper(position_manager=position_manager, key='position_mapper_test'),
        ])
    )

    cropper_1 = eco.Variable(
        eco.Compose(
            eb.Cropper(),
            (
                eco.Sequential([
                    eco.DataReduce('image_1'),
                    eco.Atomic(key=0)
                ]),
                (10, 10, 20, 20))
        ),
    )

    pipeline = eco.Sequential([
        pipeline,
        eco.DataSpread(['image_0', 'image_1']),
        eco.Concatenate([cropper_0, cropper_1]),
        eco.DataSpread(['cropped_0', 'cropped_1'])
    ])
    pipeline.update()

    data_2 = pipeline.use()
    assert data_2['cropped_0'].shape[1] < 300

    return None


def render_test():
    import epta.core.base_ops as eco
    import epta.tools.renderers as er
    import numpy as np

    class CustomRenderer(er.BaseRenderer):
        def render(self, image: 'np.ndarray', *args, **kwargs):
            if image is not None:
                print(image.shape)
                return None
            else:
                print('Got nothing:', image, *args)
                return None, 1

    cr = CustomRenderer()

    sm = eco.Compose(
        lambda r, inp: r(*inp),
        (
            eco.Wrapper(cr),  # -> cr
            eco.Sequential([
                cr,  # -> None
                cr,  # -> (None, 1)
                eco.InputUnpack(cr)  # -> (None, 1)
            ]),  # -> (None, 1)
        ),
    )
    sm.use(np.zeros((1, 1, 3)))

    return None


if __name__ == '__main__':
    mapper_test()
    hooker_test()
    cropper_test()
    render_test()

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from cryptography.hazmat.primitives.asymmetric import ec

import rfc3161ng.api as rfc3161_api


_EC_VERIFY_ERROR = "ECPublicKey.verify() takes 3 positional arguments but 4 were given"


def _check_timestamp_with_ec_support(
    tst, certificate=None, data=None, digest=None, hashname=None, nonce=None
):
    hashname = hashname or "sha1"
    hashobj = rfc3161_api.hashlib.new(hashname)
    if digest is None:
        if not data:
            raise ValueError("check_timestamp requires data or digest argument")
        hashobj.update(data)
        digest = hashobj.digest()

    if not isinstance(tst, rfc3161_api.rfc3161ng.TimeStampToken):
        tst, substrate = rfc3161_api.decoder.decode(
            tst, asn1Spec=rfc3161_api.rfc3161ng.TimeStampToken()
        )
        if substrate:
            raise ValueError("extra data after tst")

    signed_data = tst.content
    certificate = rfc3161_api.load_certificate(signed_data, certificate)

    if nonce is not None and int(tst.tst_info["nonce"]) != int(nonce):
        raise ValueError("nonce is different or missing")

    message_imprint = tst.tst_info.message_imprint
    if (
        message_imprint.hash_algorithm[0] != rfc3161_api.get_hash_oid(hashname)
        or bytes(message_imprint.hashed_message) != digest
    ):
        raise ValueError("Message imprint mismatch")

    if not len(signed_data["signerInfos"]):
        raise ValueError("No signature")

    signer_info = signed_data["signerInfos"][0]
    if tst.content["contentInfo"]["contentType"] != rfc3161_api.rfc3161ng.id_ct_TSTInfo:
        raise ValueError(
            "Signed content type is wrong: %s != %s"
            % (
                tst.content["contentInfo"]["contentType"],
                rfc3161_api.rfc3161ng.id_ct_TSTInfo,
            )
        )

    content = bytes(
        rfc3161_api.decoder.decode(
            bytes(tst.content["contentInfo"]["content"]),
            asn1Spec=rfc3161_api.univ.OctetString(),
        )[0]
    )

    signer_digest_algorithm = signer_info["digestAlgorithm"]["algorithm"]
    signer_hash_name = rfc3161_api.get_hash_from_oid(signer_digest_algorithm)

    if len(signer_info["authenticatedAttributes"]):
        authenticated_attributes = signer_info["authenticatedAttributes"]
        signer_hash_class = rfc3161_api.get_hash_class_from_oid(signer_digest_algorithm)
        content_digest = signer_hash_class(content).digest()
        for authenticated_attribute in authenticated_attributes:
            if authenticated_attribute[0] == rfc3161_api.id_attribute_messageDigest:
                signed_digest = bytes(
                    rfc3161_api.decoder.decode(
                        bytes(authenticated_attribute[1][0]),
                        asn1Spec=rfc3161_api.univ.OctetString(),
                    )[0]
                )
                if signed_digest != content_digest:
                    raise ValueError("Content digest != signed digest")

                signed_attributes_set = rfc3161_api.univ.SetOf()
                for index, attr in enumerate(authenticated_attributes):
                    signed_attributes_set.setComponentByPosition(index, attr)
                signed_payload = rfc3161_api.encoder.encode(signed_attributes_set)
                break
        else:
            raise ValueError("No signed digest")
    else:
        signed_payload = content

    signature = bytes(signer_info["encryptedDigest"])
    public_key = certificate.public_key()
    hash_family = getattr(rfc3161_api.hashes, signer_hash_name.upper())
    hash_algo = hash_family()

    if isinstance(public_key, ec.EllipticCurvePublicKey):
        public_key.verify(signature, signed_payload, ec.ECDSA(hash_algo))
    else:
        public_key.verify(
            signature,
            signed_payload,
            rfc3161_api.padding.PKCS1v15(),
            hash_algo,
        )
    return True


def patch_rfc3161ng_ec_compat():
    if getattr(rfc3161_api, "_fit_ec_compat_patched", False):
        return

    original_check_timestamp = rfc3161_api.check_timestamp

    def _patched_check_timestamp(*args, **kwargs):
        try:
            return original_check_timestamp(*args, **kwargs)
        except TypeError as exc:
            if _EC_VERIFY_ERROR not in str(exc):
                raise
            return _check_timestamp_with_ec_support(*args, **kwargs)

    rfc3161_api.check_timestamp = _patched_check_timestamp
    rfc3161_api._fit_ec_compat_patched = True
